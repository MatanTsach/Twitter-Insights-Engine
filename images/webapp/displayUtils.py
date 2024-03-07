import logging

def visualize_insights(insights, keywords, source):
    raw_html = f"""
            <div class='source'>
            <p>Insights for keywords: <span style='color: #1DA1F2;'>{keywords}</span>
                From: <span style='color: #1DA1F2;'>{source}</span></p>\n
            </div>
             """

    for insight in insights:
        insight_type = insight.get("type")

        if insight_type == 'dict':
            raw_html += f"<h2>{insight.get('title')}</h2>\n"
            raw_html += "<ul class='list'>\n"
            for data in insight.get("data"):
                raw_html += "<li class='card'>\n"
                for key, value in data.items():
                    raw_html += f"<p><b>{key}:</b> {value}</p>\n"
                raw_html += "</li>\n"
            raw_html += "</ul>\n"
        elif insight_type == 'image':
            raw_html += f"<div class='image'>\n"
            raw_html += f"<h2>{insight.get('title')}</h2>\n"
            raw_html += f"<img src='static/analyzer-images/{insight.get('name')}' alt='Image'>\n"
            raw_html += "</div>\n"
        else:
            logging.warning(f"Unknown insight type: {insight_type}")

    return raw_html
