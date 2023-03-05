## NOTE
### The Original Developers are no longer in a position to maintain this project. But we would still like to keep the project alive, thus any open source contribution from the community is more than welcome.


<br>

# Chegg-Scrapper



Download Chegg homework-help questions to html files, these html files are self sufficient, you don't need account access to load them

<details open>
    <summary>Details</summary>
    <li>
		All files are saved to html document.
    </li>
    <li>
        You will not need your chegg account to open these files later.
    </li>
</details>



## USE-CASES


* <details>
    <summary style='bold'>In Bots</summary>
    <l1>
        You can share your chegg subscription with your friends, eg: by making discord bot
    </l1>
    </details> 

* Saving Chegg Questions Locally


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
          <code>document.cookie</code>
      </ul>
      <ul>
          <li>paste yout cookie from console into cookie.txt (without <code>"</code>)</li>
      </ul>
  </details>

  ​	Or

  <details>
      <summary>Using Chrome Extenstion</summary>
      <ul>
          <li>Log-in to chegg in your web browser</li>
      </ul>
      <ul>
          <li>Open Extension (Example) <a href='https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg'>EditThisCookie</a></li>
      </ul>
      <ul>
          <li>Click Export and paste in cookie.txt</li>
      </ul>
  </details>

* You may also need to change user-agent

  * Open conf.json and edit user_agent

    * Find your browser user agent

      * Open [What's My User Agent](https://whatmyuseragent.com/) 

        Or

      * Open Browser console and run 

        ``console.log(navigator.userAgent)``



## Usage:

* If you are new to python go [here](NOOB.md)

* Run the `Downloader.py` Script

  ```console
  $ python Downloader.py
  
  Enter url of the homework-help:
  ```

* Arguments

  ```
  ALL ARGUMENTS ARE OPTIONAL
  -u or --url      >   URL of Chegg
  -c or --cookie   >   Path of Cookie file (Defualt: cookie.txt)
  -s or --save     >   file path, where you want to save, put inside " "
  ```
  
  
  
   

