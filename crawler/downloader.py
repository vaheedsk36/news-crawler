import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def extract_file_id_from_gdrive_url(url):
    """Extract the file ID from a Google Drive sharing URL."""
    parsed_url = urlparse(url)
    if "drive.google.com" in parsed_url.netloc:
        path_parts = parsed_url.path.split('/')
        if len(path_parts) >= 4:
            file_id = path_parts[3]
            return file_id
    return None

def download_links_from_page(url,publisher_name, download_path="downloads"):
    try:
        # Fetch the webpage
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Create a folder for downloads if it doesn't exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        # Find all paragraphs with <a> tags inside them
        paragraphs_with_links = soup.find_all('p')
        paragraphs_with_links = [p for p in paragraphs_with_links if p.find('a')]
        
        # Process each <p> tag containing <a> tags
        for p in paragraphs_with_links:
            p_text = p.get_text(strip=True).split(":")[0]

            links = p.find_all('a', href=True)

            for link in links:
                href = link['href']
                full_url = urljoin(url, href)
                file_id = extract_file_id_from_gdrive_url(full_url)
                a_text = link.get_text(strip=True)
                file_name = f"{publisher_name}||{p_text}||{a_text}.pdf".replace(" ", "_")
                if file_id:
                    direct_download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                    file_path = os.path.join(download_path, file_name)
                    if os.path.exists(file_path):
                        base, ext = os.path.splitext(file_name)
                        counter = 1
                        while os.path.exists(file_path):
                            file_name = f"{base}_{counter}{ext}"
                            file_path = os.path.join(download_path, file_name)
                            counter += 1
                    
                    print(f"Downloading: {direct_download_url}")
                    file_response = requests.get(direct_download_url)
                    file_response.raise_for_status()

                    # Save the file to disk
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                    print(f"Saved to: {file_path}")
                else:
                    print(f"Skipping non-Google Drive link: {full_url}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    target_url = "https://www.dailyepaper.in/the-free-press-journal-epaper-download/"
    publisher_name = "the_free_press_journal"
    download_links_from_page(target_url,publisher_name)