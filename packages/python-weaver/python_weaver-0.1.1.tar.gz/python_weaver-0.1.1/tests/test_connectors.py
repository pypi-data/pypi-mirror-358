import pytest
import requests
from pathlib import Path
from weaver.connectors.pdf_reader import PDFReader
from weaver.connectors.url_scraper import URLScraper
from weaver.exceptions import ConnectorError
import responses

def test_pdf_reader(tmp_path):
    # Create a simple PDF
    from PyPDF2 import PdfWriter
    pdf_path = tmp_path / "doc.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    text = PDFReader().ingest(str(pdf_path))
    assert isinstance(text, str)

@responses.activate
def test_url_scraper_success(tmp_path):
    url = "http://example.com/test"
    html = "<html><body><p>Hello World</p></body></html>"
    responses.add(responses.GET, url, body=html, status=200)
    text = URLScraper().ingest(url)
    assert "Hello World" in text

@responses.activate
def test_url_scraper_failure(tmp_path):
    url = "http://example.com/err"
    responses.add(responses.GET, url, status=500)
    with pytest.raises(ConnectorError):
        URLScraper().ingest(url)
