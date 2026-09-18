"""
omr_processor.py
================
OpenCV-based OMR (Optical Mark Recognition) engine.

Steps:
  1. Load & pre-process image (grayscale, blur, threshold)
  2. Warp perspective to flatten/deskew the sheet
  3. Divide into Q×4 bubble grid
  4. Detect filled bubble per row → student answer
  5. Compare with answer key → score, overlay image
"""

import cv2
import numpy as np
import base64
from typing import Optional


# ─────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────

def process_omr(image_path: str, answer_key: dict, config: dict) -> dict:
    """
    Process an OMR sheet image and return grading results.

    Parameters
    ----------
    image_path   : path to uploaded image
    answer_key   : {1: 'A', 2: 'B', ...}  (1-indexed)
    config       : {
                      'total_questions': int,
                      'options': int,           # 4 = A/B/C/D
                      'negative_marking': float # 0 = disabled
                   }

    Returns
    -------
    dict with keys: answers, score, correct, wrong, unattempted,
                    total, overlay_image (base64 PNG)
    """
    total_q   = config.get('total_questions', len(answer_key))
    n_options = config.get('options', 4)
    neg_mark  = config.get('negative_marking', 0.0)
    option_labels = ['A', 'B', 'C', 'D', 'E'][:n_options]

    # ── 1. Load image ──────────────────────────────────────────────
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot load image: {image_path}")

    # ── 2. Pre-process ─────────────────────────────────────────────
    gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh  = cv2.threshold(blurred, 0, 255,
                            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # ── 3. Find sheet boundary & warp ──────────────────────────────
    warped_gray, warped_color = _warp_sheet(gray, img, thresh)

    # ── 4. Build bubble grid ───────────────────────────────────────
    h, w = warped_gray.shape
    # Re-threshold the warped image
    _, wb_thresh = cv2.threshold(
        cv2.GaussianBlur(warped_gray, (5, 5), 0),
        0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    student_answers = {}  # {question_number: 'A'/'B'/.../'?'}

    # Divide into rows (questions) × cols (options)
    row_h = h // total_q
    col_w = w // n_options

    for q in range(total_q):
        question_num = q + 1
        y_start = q * row_h
        y_end   = y_start + row_h

        fill_counts = []
        for opt in range(n_options):
            x_start = opt * col_w
            x_end   = x_start + col_w
            roi     = wb_thresh[y_start:y_end, x_start:x_end]
            fill_counts.append(int(np.sum(roi > 0)))

        max_fill   = max(fill_counts)
        min_fill   = min(fill_counts)
        threshold  = max_fill * 0.55   # at least 55 % of the max

        # Detect selection
        marked = [i for i, fc in enumerate(fill_counts) if fc >= threshold and fc > min_fill + 50]

        if len(marked) == 1:
            student_answers[question_num] = option_labels[marked[0]]
        elif len(marked) == 0:
            student_answers[question_num] = '?'   # unattempted
        else:
            student_answers[question_num] = 'M'   # multiple marked

    # ── 5. Score calculation ───────────────────────────────────────
    correct     = 0
    wrong       = 0
    unattempted = 0

    for q_num, correct_ans in answer_key.items():
        student_ans = student_answers.get(int(q_num), '?')
        if student_ans == '?':
            unattempted += 1
        elif student_ans == correct_ans.upper():
            correct += 1
        else:
            wrong += 1

    score = correct - (neg_mark * wrong)
    score = max(0, score)   # clamp to 0

    # ── 6. Generate overlay ────────────────────────────────────────
    overlay_b64 = _draw_overlay(
        warped_color, student_answers, answer_key,
        total_q, n_options, option_labels
    )

    # ── 7. Build per-question table ────────────────────────────────
    questions_table = []
    for q_num in range(1, total_q + 1):
        correct_ans = answer_key.get(str(q_num), answer_key.get(q_num, '?'))
        student_ans = student_answers.get(q_num, '?')
        if student_ans == '?':
            result = 'unattempted'
        elif student_ans == str(correct_ans).upper():
            result = 'correct'
        else:
            result = 'wrong'
        questions_table.append({
            'q':          q_num,
            'correct':    str(correct_ans).upper(),
            'student':    student_ans,
            'result':     result,
        })

    return {
        'answers':      student_answers,
        'score':        round(score, 2),
        'correct':      correct,
        'wrong':        wrong,
        'unattempted':  unattempted,
        'total':        len(answer_key),
        'percentage':   round((correct / len(answer_key)) * 100, 1),
        'overlay_image': overlay_b64,
        'questions_table': questions_table,
    }


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _order_points(pts):
    """Return points in order: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype='float32')
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left  (smallest sum)
    rect[2] = pts[np.argmax(s)]   # bot-right (largest sum)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bot-left
    return rect


def _four_point_transform(image, pts):
    """Perspective-warp image to a top-down rectangle."""
    rect = _order_points(pts)
    (tl, tr, br, bl) = rect
    widthA  = np.linalg.norm(br - bl)
    widthB  = np.linalg.norm(tr - tl)
    maxW    = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxH    = max(int(heightA), int(heightB))
    dst = np.array([[0, 0], [maxW - 1, 0],
                    [maxW - 1, maxH - 1], [0, maxH - 1]], dtype='float32')
    M       = cv2.getPerspectiveTransform(rect, dst)
    warped  = cv2.warpPerspective(image, M, (maxW, maxH))
    return warped


def _warp_sheet(gray, color, thresh):
    """
    Find the largest rectangular contour (the answer sheet) and warp it.
    Falls back to a resized crop of the full image if no sheet contour found.
    """
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts    = sorted(cnts, key=cv2.contourArea, reverse=True)

    sheet_cnt = None
    for c in cnts:
        peri   = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            sheet_cnt = approx
            break

    if sheet_cnt is not None:
        pts          = sheet_cnt.reshape(4, 2).astype('float32')
        warped_gray  = _four_point_transform(gray,  pts)
        warped_color = _four_point_transform(color, pts)
    else:
        # Fallback: use the entire image
        warped_gray  = cv2.resize(gray,  (600, 800))
        warped_color = cv2.resize(color, (600, 800))

    return warped_gray, warped_color


def _draw_overlay(warped_color, student_answers, answer_key,
                  total_q, n_options, option_labels):
    """
    Draw colored circles on detected bubbles:
      green  = correctly filled
      red    = wrongly filled
      grey   = unattempted
      orange = unfilled but was the correct answer
    """
    overlay = warped_color.copy()
    h, w    = overlay.shape[:2]
    row_h   = h // total_q
    col_w   = w // n_options

    GREEN  = (0, 200, 80)
    RED    = (0, 60, 220)
    ORANGE = (0, 165, 255)
    GREY   = (150, 150, 150)

    for q in range(total_q):
        q_num       = q + 1
        student_ans = student_answers.get(q_num, '?')
        correct_ans = str(answer_key.get(str(q_num), answer_key.get(q_num, ''))).upper()

        cy = q * row_h + row_h // 2

        for opt_idx, label in enumerate(option_labels):
            cx    = opt_idx * col_w + col_w // 2
            r     = min(row_h, col_w) // 3

            filled = (student_ans == label)
            correct_here = (label == correct_ans)

            if filled and correct_here:
                color = GREEN
            elif filled and not correct_here:
                color = RED
            elif not filled and correct_here and student_ans != '?':
                color = ORANGE
            else:
                continue   # don't draw empty, non-relevant bubbles

            cv2.circle(overlay, (cx, cy), r, color, 3)
            if filled:
                cv2.circle(overlay, (cx, cy), r - 4, color, -1)

    # Encode to base64 PNG
    _, buf = cv2.imencode('.png', overlay)
    return base64.b64encode(buf).decode('utf-8')
