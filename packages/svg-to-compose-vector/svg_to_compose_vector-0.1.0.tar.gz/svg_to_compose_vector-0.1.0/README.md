# Svg to Compose-Vector

Convert SVG files to Kotlin Compose ImageVector code with high fidelity and production-ready output.

`svg-to-compose-vector` is a Python command-line tool that transforms SVG graphics into Compose ImageVector Kotlin code. It supports advanced SVG features including paths, shapes, gradients, transforms, and strokes, generating clean, optimized Compose code.

[Installation](#installation) • [Usage](#usage) • [Features](#features) • [Examples](#examples)

## Features

* **Complete SVG Support**: Handles paths, basic shapes (rect, circle, ellipse, line, polygon), groups, transforms, gradients, and strokes
* **High Fidelity Conversion**: Mathematically precise shape-to-path conversion with proper coordinate handling
* **Production-Ready Output**: Generates clean Kotlin code following Compose best practices with optimal parameter usage
* **Flexible Templates**: Built-in templates for different use cases (val declarations, composable functions, icon objects)
* **Advanced Color Support**: Yes support for hex, RGB, HSL, named colors, and gradients (linear and radial)
* **Smart Optimizations**: Uses Compose built-in colors (Color.Red vs Color(0xFFFF0000)) and omits default parameters
* **Comprehensive Error Handling**: Clear warnings for unsupported SVG features with graceful degradation
* **Batch Processing**: Convert entire directories of SVG files at once

## Quick Example

Convert an SVG file to Compose ImageVector code:

```bash
svg2compose convert icon.svg
```

Output:
```kotlin
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp

ImageVector.Builder(
  name = "Icon",
  defaultWidth = 24f.dp,
  defaultHeight = 24f.dp,
  viewportWidth = 24f,
  viewportHeight = 24f,
).apply {
  path(fill = SolidColor(Color.Black)) {
    moveTo(12f, 2f)
    lineTo(22f, 12f)
    lineTo(12f, 22f)
    lineTo(2f, 12f)
    close()
  }
}.build()
```

## Installation

### Using uv (Recommended)

```bash
git clone https://github.com/chachako/svg-to-compose-vector.git
cd svg-to-compose-vector
uv sync
uv run python -m src.cli --help
```

### Using pip with virtual environment

```bash
git clone https://github.com/chachako/svg-to-compose-vector.git
cd svg-to-compose-vector
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
svg2compose --help
```

## Usage

### Basic conversion

```bash
# Convert to stdout
svg2compose convert icon.svg

# Convert to file
svg2compose convert icon.svg -o Icon.kt

# Specify icon name
svg2compose convert icon.svg -n HomeIcon
```

### Using templates

```bash
# List available templates
svg2compose templates

# Use composable function template
svg2compose convert icon.svg -t composable_function -o HomeIcon.kt

# Use val declaration template
svg2compose convert icon.svg -t val_declaration -o Icons.kt

# Use custom template file
svg2compose convert icon.svg -t my_template.j2 -o CustomIcon.kt
```

### Batch processing

```bash
# Convert all SVG files in a directory
svg2compose batch icons/ output/

# With custom naming pattern
svg2compose batch icons/ output/ --naming "Icon{name}"

# Using specific template
svg2compose batch icons/ output/ -t composable_function
```

### File information

```bash
# Show SVG file details
svg2compose info icon.svg
```

## Supported SVG Features

| Feature | Support | Notes |
|---------|---------|-------|
| **Paths** | ✅ Yes | All path commands (M, L, C, A, Z, etc.) |
| **Basic Shapes** | ✅ Yes | rect, circle, ellipse, line, polygon, polyline |
| **Groups & Transforms** | ✅ Yes | translate, scale, rotate, matrix decomposition |
| **Colors** | ✅ Yes | hex, rgb, hsl, named colors with alpha support |
| **Gradients** | ✅ Yes | Linear and radial gradients with multiple stops |
| **Strokes** | ✅ Yes | Width, opacity, caps, joins, gradient strokes |
| **ClipPath** | ✅ Yes | Basic clipPath support for groups |
| **Text** | ⚠️ No | Text elements show warnings (not supported by Compose ImageVector) |
| **Filters** | ⚠️ No | Filter effects show warnings (not supported by Compose ImageVector) |
| **Animations** | ⚠️ No | Animation elements show warnings (static conversion only) |

## Templates

### Built-in Templates

1. **default**: Basic ImageVector.Builder code
2. **val_declaration**: Generates `val iconName: ImageVector = ...`
3. **composable_function**: Generates `@Composable fun IconName(): ImageVector`
4. **icon_object**: Generates icon object structure

### Custom Templates

Create custom Jinja2 templates for specialized output formats:

```jinja2
// Custom template example
val {{ name }}: ImageVector by lazy {
  {{ build_code }}
}
```

## Advanced Examples

### Complex SVG with gradients and transforms

```bash
svg2compose convert complex_icon.svg -t composable_function
```

Generated output handles gradients and transforms automatically:
```kotlin
@Composable
fun ComplexIcon(): ImageVector {
  return ImageVector.Builder(
    name = "ComplexIcon",
    defaultWidth = 48f.dp,
    defaultHeight = 48f.dp,
    viewportWidth = 48f,
    viewportHeight = 48f,
  ).apply {
    group(
      name = "rotated-group",
      rotate = 45f,
      pivotX = 24f,
      pivotY = 24f,
    ) {
      path(
        fill = Brush.linearGradient(
          colorStops = arrayOf(
            0f to Color.Red,
            0.5f to Color.Yellow,
            1f to Color.Blue,
          ),
          start = Offset(0f, 0f),
          end = Offset(48f, 48f),
        ),
      ) {
        // path data...
      }
    }
  }.build()
}
```

## Performance

`svg-to-compose-vector` is designed for efficiency:

* **Fast parsing**: Regex-based tokenization with compiled patterns
* **Memory efficient**: Minimal object creation with immutable dataclasses
* **Batch processing**: Process hundreds of icons in seconds
* **Smart optimization**: Only generates necessary parameters

## Configuration

Use configuration files for consistent settings across projects:

```json
{
  "template": "composable_function",
  "indent_size": 2,
  "use_named_colors": true,
  "optimize_output": true
}
```

```bash
svg2compose convert icon.svg -c config.json
```

## Development

```bash
git clone https://github.com/chachako/svg-to-compose-vector.git
cd svg-to-compose-vector

# Setup development environment
uv sync --dev

# Run tests
uv run pytest

# Code formatting and linting
uv run ruff check
uv run ruff format
```

## Requirements

* Python 3.13+
* Dependencies: jinja2, click (automatically installed)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

This project was inspired by the [Valkyrie](https://github.com/ComposeGears/Valkyrie) project.
