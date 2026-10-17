# नवरात्र उत्सव २०२६ - जमा-खर्च हिशोब

- `Navratri_2026_Hishob.pdf` - हा अंतिम अहवाल आहे
- `data.py` - वहीतील सर्व नोंदी, खर्च आणि बँक जमा नोंदी
- `build.py` + `style.css` - या फाइल्स `hishob.html` तयार करतात
- `render.js` - HTML वरून PDF तयार करते

PDF पुन्हा तयार करण्यासाठी:

    python3 build.py && NODE_PATH=$(npm root -g) node render.js

(Mukta फॉन्ट लागतो.)
