# Chegg-Scrapper



## USE-CASES

* #### CAN BE USED IN BOTS

* #### Saving Chegg Questions Locally



## Setup:

* Download [latest release](https://github.com/ThreeGiantNoobs/chegg-scraper/releases/latest)

* Install requirements 
  `pip install -r requirements.txt`

* Save your cookie in file cookie.txt (preferably)

  <details>
      <summary>Using Browser Console</summary>
      <ul>
          <li>Log-in to chegg in your browser and open up the developer console. (cmd-shift-c or ctrl-shift-i)</li>
      </ul>
      <ul>
          <li>Grab your cookies by typing </li>
          <code>document.txt</code>
      </ul>
      <ul>
          <li>paste yout cookie from console into cookie.txt (without <code>"</code>)</li>
      </ul>
  </details>

  ​	Or

  <details>
      <summary>Using Chrome Extenstion</summary>
      <ul>
          <li>Log-in to chegg in your browser</li>
      </ul>
      <ul>
          <li>Open Extension (Example) <a href='https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg'>EditThisCookie</a></li>
      </ul>
      <ul>
          <li>Click Export and paste in cookie.txt</li>
      </ul>
  </details>



## Usage:

* Run the `Downloader.py` Script

  ```console
  $ python Downloader.py
  
  Enter url of the homework-help:
  ```

* Arguments

  ```
  ALL ARGUMENTS ARE OPTIONAL
  -u or -url      >   URL of Chegg
  -c or -cookie   >   Path of Cookie file (Defualt: cookie.txt)
  ```

  

  

