"""
Builds a small, self-contained HTML report out of the healing events
collected during a pytest run. No external reporting library required.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List


def _row_css_class(event: Dict) -> str:
    if event.get("healing_result") == "SUCCESS":
        return "healed"
    if event.get("final_status") == "FAILED":
        return "failed"
    return "passed"


def _format_confidence(event: Dict) -> str:
    confidence = event.get("confidence")
    if confidence is None:
        return "-"
    try:
        return f"{float(confidence) * 100:.0f}%"
    except (TypeError, ValueError):
        return str(confidence)


def generate_html_report(events: List[Dict], output_path: Path) -> None:
    """Writes a simple HTML table report to `output_path`."""

    rows_html = ""
    for event in events:
        rows_html += f"""
        <tr class="{_row_css_class(event)}">
            <td>{event.get('description') or '-'}</td>
            <td>{event.get('original_status') or '-'}</td>
            <td>{'YES' if event.get('healing_attempted') else 'NO'}</td>
            <td><code>{event.get('original_locator') or '-'}</code></td>
            <td><code>{event.get('healed_locator') or '-'}</code></td>
            <td>{_format_confidence(event)}</td>
            <td>{event.get('healing_result') or '-'}</td>
            <td>{event.get('final_status') or '-'}</td>
        </tr>"""

    if not rows_html:
        rows_html = '<tr><td colspan="8">No healing events were recorded in this run.</td></tr>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Self-Healing Test Mesh - Report</title>
<style>
    body {{ font-family: Arial, sans-serif; margin: 30px; background: #f7f7f9; color: #222; }}
    h1 {{ margin-bottom: 4px; }}
    p.meta {{ color: #666; margin-top: 0; }}
    table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
    th, td {{ border: 1px solid #e2e2e2; padding: 10px 12px; text-align: left; font-size: 14px; vertical-align: top; }}
    th {{ background: #1f2937; color: white; }}
    tr.healed {{ background: #eaffea; }}
    tr.failed {{ background: #ffecec; }}
    code {{ font-size: 13px; background: #f1f1f1; padding: 2px 4px; border-radius: 3px; }}
</style>
</head>
<body>
<h1>Self-Healing Test Mesh</h1>
<p class="meta">Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<table>
<tr>
    <th>Test / Action</th>
    <th>Original Status</th>
    <th>Healing Attempted</th>
    <th>Original Locator</th>
    <th>Healed Locator</th>
    <th>Confidence</th>
    <th>Healing Result</th>
    <th>Final Status</th>
</tr>
{rows_html}
</table>
</body>
</html>
"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
