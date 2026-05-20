from PIL import Image, ImageDraw, ImageFont, ImageFilter

SIZE = 1024
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Soft cream background with rounded corners
draw.rounded_rectangle([(0, 0), (SIZE, SIZE)], radius=220, fill=(251, 248, 243, 255))

# Sage circle in center
cx, cy = SIZE // 2, SIZE // 2
r = 380
draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(122, 155, 118, 255))

# Inner lighter circle for depth
r2 = 340
draw.ellipse([(cx - r2, cy - r2), (cx + r2, cy + r2)], fill=(168, 184, 155, 255))

# Brain emoji
try:
    font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 480)
    bbox = draw.textbbox((0, 0), "🧠", font=font, embedded_color=True)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((SIZE - w) // 2 - bbox[0], (SIZE - h) // 2 - bbox[1]),
        "🧠",
        font=font,
        embedded_color=True,
    )
except Exception as e:
    print(f"Emoji fallback: {e}")

img.save("icon.png")
print("Saved icon.png")