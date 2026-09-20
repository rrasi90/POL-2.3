# POL Component Specifications

**Date:** 2026-09-20  
**Status:** DRAFT

---

## 1. Button Components

### Primary Button
```
Width: Auto (min 120px)
Height: 44px (mobile), 40px (desktop)
Padding: 0 24px
Font: 14px/600 Vazirmatn
Color: White text on #1E40AF bg
Hover: #1E3A8A bg
Active: #1E3388 bg
Disabled: 50% opacity, no pointer
Border-radius: 6px
```

### Secondary Button
```
Same dimensions as Primary
Color: #1E40AF text on white bg
Border: 1px solid #E5E7EB
Hover: #F9FAFB bg
```

### Danger Button
```
Same dimensions as Primary
Color: White text on #DC2626 bg
Hover: #B91C1C bg
```

### Ghost Button
```
Same dimensions as Primary
Color: #6B7280 text, no bg
Hover: #F3F4F6 bg
```

### Icon Button
```
Width/Height: 40px
Border-radius: 8px
Icon: 20px, centered
```

---

## 2. Input Components

### Text Input
```
Height: 44px
Padding: 0 16px
Font: 14px/400 Vazirmatn
Border: 1px solid #D1D5DB
Border-radius: 6px
Focus: 2px ring #3B82F6, border #3B82F6
Error: Border #EF4444, message below in #EF4444
```

### Select Dropdown
```
Same as Text Input
Arrow: Chevron down icon (right side in RTL)
Options: 44px height per option
```

### Search Input
```
Same as Text Input
Prefix: Search icon (magnifying glass)
Clear button: X icon when value present
```

### Quantity Input
```
Width: 120px
Layout: [-] [input] [+]
Button: 36px width, 44px height
Input: Center-aligned, 14px/600
```

---

## 3. Card Components

### Product Card
```
Width: Full grid column
Padding: 16px
Border: 1px solid #E5E7EB
Border-radius: 8px
Shadow: --shadow-sm
Image area: 120px height, bg #F3F4F6
Content: Name (14px/600), Brand (12px/400 #6B7280), 
         Pack size (12px/400 #9CA3AF), 
         Price (14px/700), Add button
```

### Order Card
```
Width: Full list width
Padding: 16px
Border: 1px solid #E5E7EB
Border-radius: 8px
Layout: Flex row (RTL: row-reverse)
Left: Order number (14px/600), Date (12px/400 #6B7280)
Right: Status badge, Total (14px/700)
```

### KPI Card
```
Width: Flex-1 (min 200px)
Padding: 20px
Border-radius: 8px
Shadow: --shadow-sm
Title: 12px/400 #6B7280 uppercase
Value: 28px/700
Trend: 12px/500, green up arrow or red down arrow
```

---

## 4. Badge Components

### Status Badge
```
Height: 24px
Padding: 0 10px
Font: 11px/500
Border-radius: 12px (full)

Variants:
- CREATED: bg #DBEAFE, text #1D4ED8
- SUBMITTED: bg #DBEAFE, text #1D4ED8
- ACCEPTED: bg #E0E7FF, text #4338CA
- PREPARING: bg #FEF9C3, text #A16207
- DISPATCHED: bg #F3E8FF, text #7C3AED
- DELIVERED: bg #DCFCE7, text #15803D
- CANCELLED: bg #FEE2E2, text #B91C1C
- OPEN: bg #DBEAFE, text #1D4ED8
- IN_PROGRESS: bg #FEF9C3, text #A16207
- RESOLVED: bg #DCFCE7, text #15803D
```

### Priority Badge
```
Same dimensions as Status Badge

Variants:
- LOW: bg #F3F4F6, text #6B7280
- NORMAL: bg #DBEAFE, text #1D4ED8
- HIGH: bg #FEF3C7, text #92400E
- CRITICAL: bg #FEE2E2, text #B91C1C
```

---

## 5. Table Components

### Data Table
```
Header: bg #F9FAFB, font 12px/500 #6B7280, border-bottom 2px #E5E7EB
Row: height 48px, border-bottom 1px #F3F4F6
Row hover: bg #F9FAFB
Cell padding: 0 16px
Font: 14px/400
Actions column: Right-aligned (left in RTL)
```

### Sortable Header
```
Same as Table Header
Sort icon: Arrow up/down, 16px
Active sort: text #1E40AF, arrow filled
```

### Pagination
```
Height: 48px
Layout: Flex row (RTL: row-reverse)
Info: "Showing 1-50 of 123" (14px/400 #6B7280)
Controls: [Previous] [1] [2] [3] ... [Next]
Button: 36px height, border 1px #E5E7EB
Active page: bg #1E40AF, text white
```

---

## 6. Modal Components

### Confirmation Modal
```
Width: 400px
Padding: 24px
Border-radius: 12px
Shadow: --shadow-xl
Overlay: rgba(0,0,0,0.5)
Title: 18px/600
Body: 14px/400 #6B7280
Actions: Secondary + Danger buttons, right-aligned (left in RTL)
```

### Form Modal
```
Width: 560px
Padding: 24px
Header: Title + Close button
Body: Form content
Footer: Cancel + Submit buttons
```

---

## 7. Navigation Components

### Sidebar
```
Width: 256px (expanded), 64px (collapsed)
Bg: #111827 (dark)
Item height: 44px
Item padding: 0 16px
Icon: 20px, white/gray-400
Label: 14px/400 white/gray-400
Active: bg #1E40AF, text white
Hover: bg rgba(255,255,255,0.1)
```

### Top Bar
```
Height: 64px
Bg: white
Border-bottom: 1px #E5E7EB
Padding: 0 24px
Logo: Left (right in RTL)
Search: Center, max-width 400px
Actions: Right (left in RTL)
```

### Tab Bar
```
Height: 48px
Item: Padding 0 16px, font 14px/500
Active: border-bottom 2px #1E40AF, text #1E40AF
Inactive: text #6B7280
Hover: text #111827
```

---

## 8. Form Components

### Address Form
```
Fields:
- Province: Select dropdown (31 provinces)
- City: Select dropdown (filtered by province)
- Address: Textarea, 3 rows
- Postal code: Input, 10 digits, LTR
- Phone: Input, 11 digits, LTR
```

### Date Picker (Jalali)
```
Calendar: 7-column grid
Header: Month/Year with nav arrows
Days: 36px circles
Selected: bg #1E40AF, text white
Today: border #1E40AF
Disabled: text #D1D5DB
```

---

## 9. Empty State Component

```
Layout: Centered column
Illustration: 120x120px SVG, light colors
Title: 18px/600 #111827
Description: 14px/400 #6B7280, max-width 300px
CTA: Primary button
```

---

## 10. Loading State Components

### Skeleton Loader
```
Bg: linear-gradient(90deg, #F3F4F6 25%, #E5E7EB 50%, #F3F4F6 75%)
Animation: 1.5s infinite
Border-radius: 4px
Variants: Text (h/w), Circle, Rectangle
```

### Spinner
```
Size: 24px (small), 40px (large)
Color: #1E40AF
Animation: 1s linear infinite rotation
```
