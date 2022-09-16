# Add to sitemap++ 
Add to sitemap++ is a [BURP](https://portswigger.net/burp) extension that can read URLs from files or clipboard and add the discovered information on the site map of the selected host(s).

Information doesn’t need to be structured, only readable strings. Regular expressions will handle the information.

Extension can handle many kinds of files but must be in URL structure (example _https://www.example.com/_), tested files are:
- plaintext files
- xml files
- zip files (containing text files) 
- docx, xlsx, pptx
- Vulnerability scanner files from the Nessus, Acunetix, Dirb and Nikto (with htm output) maybe more only tested on these 😊

Install Extension:
```
Burp Suite > Extender > Extensions > Add > Extension type: Python > Extension file: Add_Sitemap++.py > Next
```
>Credits for [Nixawk's script](https://github.com/nixawk/hello-python2/blob/master/burpsuite/sitemap-Import_links.py) helped me a lot. But I needed more files and clipboard with regex to be supported. Regex found on internet multiple locations (credits for the founder) can’t find it anymore, but you can try on https://regex101.com/r/pNc2cC/1 and fixed freely 😊. 

Demo:



https://user-images.githubusercontent.com/49560894/190729659-4cfa20d8-4434-43c2-8456-30d99a630c19.mp4

