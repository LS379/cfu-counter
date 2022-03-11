const { execFile } = require("child_process");
const fs = require("fs");
const path = require("path");
const express = require("express");
const fileUpload = require("express-fileupload");
const cors = require("cors");

const app = express();


app.use(cors());
app.use(fileUpload());
app.use(express.static(path.join(__dirname, "../build")));
app.use("/file", express.static(path.join(__dirname, "data")));


app.post("/upload", function(req, res) {
  if (!req.files.newFile) {
    return res.status(400).json({});
  }

  const newFile = req.files.newFile;

  newFile.mv(path.join(__dirname, `data/${newFile.name}`), function(err) {
    if (err) {
      return res.status(500).json({});
    }

    fs.writeFileSync(path.join(__dirname, `data/${newFile.name}.json`), "{}");
    res.status(200).json({});
  });
});

app.post("/save", function(req, res) {
  const { file, data } = req.body;

  fs.writeFileSync(path.join(__dirname, `data/${file}.json`), data);

  res.status(200).json({ success: true });
});

app.get("/files", (req, res) => {
  const dataFolder = path.join(__dirname, "data");
  fs.readdir(dataFolder, (err, files) => {
    const output = [];

    files.forEach((fileName) => {
      const filePath = path.join(dataFolder, fileName);

      if (fs.statSync(filePath).isDirectory() || path.extname(fileName) === ".json") {
        return;
      }

      output.push(fileName);
    });

    res.status(200).json({ files: output });
  });
});

app.get("/colonies", (req, res) => {
  const { file, x, y } = req.query;
  const params = JSON.stringify({ file, x, y })

  execFile("python", ["./server/convert.py", params], {"maxBuffer": 1024*1024*1024}, (err, data) => {
    if(err) {
      console.log(err)
    }

    res.status(200).json(data);
  })
})

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "../build/index.html"));
})


app.listen(3001, () => {
  console.log("Server started at pot 3001");
})
