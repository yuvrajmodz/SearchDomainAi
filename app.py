from flask import Flask, request, jsonify, Response, render_template
from playwright.sync_api import sync_playwright
import os
import socket
from bs4 import BeautifulSoup

app = Flask(__name__)

#╔═══════════════════════════╗
#║                                            
#║    𝗖𝗼𝗽𝘆𝗿𝗶𝗴𝗵𝘁 © 𝟮𝟬𝟮𝟰 𝗬𝗨𝗩𝗥𝗔𝗝𝗠𝗢𝗗𝗭     
#║     𝗖𝗥𝗘𝗗𝗜𝗧: 𝐌𝐀𝐓𝐑𝐈𝐗 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑      
#║                                            
#╚═══════════════════════════╝

def extract_domains(prompt_text):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
        page = context.new_page()

        # Navigate to the target page
        page.goto("https://www.domain.com/domains/ai-domain-generator?endpoint=jarvis&flow=jdomainDFE#/jdomainDFE/1")

        # Fill in the prompt text in the specific textarea field
        textarea_selector = "textarea[aria-label='A website dedicated to paintings of pets and their humans...']"
        page.fill(textarea_selector, prompt_text)

        button_selector = "#domain-ai-mfe__name-finder__submit"
        page.click(button_selector)

        loading_selector = ".MuiSkeleton-root.MuiSkeleton-text.MuiSkeleton-pulse.css-z7erpk"
        page.wait_for_selector(loading_selector, state="visible")
        page.wait_for_selector(loading_selector, state="hidden")

        page_content = page.content()
        soup = BeautifulSoup(page_content, 'html.parser')

        domains = []
        domain_spans = soup.find_all("span", class_="MuiTypography-root MuiTypography-h3 MuiCardHeader-title css-e461jq")

        for span in domain_spans:
            domain_name = span.text.strip()
            domains.append(domain_name)

        browser.close()

        return domains

def is_domain_available(domain):
    try:
        # Check if the domain has a DNS record
        socket.gethostbyname(domain)
        # If it succeeds, the domain is not available
        return False
    except socket.gaierror:
        # If it fails, the domain might be available
        return True

@app.route('/Ai-GenDomain', methods=['GET'])
def ai_gen_domain():
    prompt = request.args.get('prompt', '')
    format_type = request.args.get('format', 'json').lower()
    
    if not prompt:
        return jsonify({"error": "Prompt parameter is required."}), 400

    domains = extract_domains(prompt)

    if format_type == 'txt':
        response = "\n".join(domains)
        return Response(response, mimetype='text/plain')
    elif format_type == 'xml':
        xml_response = "<domains>" + "".join(f"<domain>{domain}</domain>" for domain in domains) + "</domains>"
        return Response(xml_response, mimetype='application/xml')
    else:
        return jsonify({"domains": domains})

@app.route('/check', methods=['GET'])
def check_domain():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Domain parameter is missing"}), 400

    # Check if the domain is available
    available = is_domain_available(domain)

    # Respond with JSON format
    return jsonify({
        "domain": domain,
        "available": available
    })
    
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5027))
    app.run(host='0.0.0.0', port=port, debug=True)