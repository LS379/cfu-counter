CFU Counter is an open-source application for automated counting of colony-forming units (CFUs) from microbiological plate images.
Developed as part of my Master’s dissertation project, it provides reproducible morphology-based image analysis for quantitative microbiology.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

**Project Structure**
cfu-counter/
│
├── src/                      # React frontend
│   ├── components/
│   ├── pages/
│   └── utils/
│
├── public/                   # Static assets
│
├── server/                   # Backend + Python analysis
│   ├── index.js              # Node.js API
│   ├── convert.py            # Colony detection module
│   ├── __init__.py
│   └── requirements.txt
│
├── config/                   # Build configuration
├── scripts/                  # Development scripts
├── package.json              # Dependencies
└── README.md


## Available Scripts

In the project directory, you can run:


### `npm start`

Runs the app in the development mode.<br>
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br>
You will also see any lint errors in the console.


### `npm run build`

Builds the app for production to the `build` folder.


### `npm run server`

Start the server. Default port `3001`.


### `npm run all`

Run the build and start the server.

### pip install -r requirements.txt
