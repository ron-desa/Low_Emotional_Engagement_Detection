# annotateApp

### Prerequisites

Google how to install these if you don't have them already.

- [Node.js](https://nodejs.org/en/) (>= 8.x, 10.x preferred)
- [npm](https://www.npmjs.com/) (>= 5.x)
- [react](https://reactjs.org/) 
- [vite](https://vitejs.dev/) [no need to install globally, but this is the bundler we use] 

### Installation

```bash
$ git clone https://github.com/AkhileshAdithya/annotateApp
$ cd annotateApp
$ npm install
```

### Running the app

```bash
$ cd annotateApp (ONLY IF YOU ARE NOT ALREADY IN THE DIRECTORY)
$ npm run dev
```

### Instructions

- On the landing page, enter the name and id of the user. The csv file will be downloaded with the id as the filename, so make sure it is unique.

- Once the name and id are entered click on the submit button. The user will be redirected to the annotation page.

- In the annotation page, first, click on the START RECORDING button. This should remove the idle message and say "recording", with a stop recording button.

- Now click on the streched BITS logo with the play button on it. This should start the video.

- Then click once on the AROUSAL VALENCE box to start the annotation on the bottom right corner of the screen. You can then use the arrow button to change the arousal and valence values which are continuously annotated. You can see the current value of the valence and arousal in the top of the screen.

- You can click on the "Download CSV" button to download the csv file with the annotations at any time. The file should also be downloaded automatically when the all the videos are completed. REMEMBER TO CLICK ON THE STOP RECORDING BUTTON AND THEN CLICK ON THE DOWNLOAD VIDEO BUTTON.