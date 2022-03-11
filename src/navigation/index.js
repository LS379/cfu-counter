import classnames from "classnames";
import React, { Component } from "react";

import state from "../state";
import styles from "./index.module.css";

export default class Navigation extends Component {
  static contextType = state;

  componentDidMount = async () => {
    const response = await fetch("http://localhost:3001/files");
    const json = await response.json();

    this.context.updateFiles(json.files);
  }

  render() {
    return (
      <div className={styles.container}>
        <div className={styles.fileButtonContainer}>
          <input
            id="newFile"
            type="file"
            name="newFile"
            onChange={this.onUpload}
            accept="image/*"
          />
          <label className={styles.fileButton} htmlFor="newFile" >
            + Upload image
          </label>
        </div>

        <div className={styles.navigation}>
          {this.renderMessage()}
          {this.context.files.map(this.renderFile)}
        </div>
      </div>
    );
  }

  renderMessage() {
    if(this.context.files.length > 0) {
      return null;
    }

    return (
      <div className={styles.message}>
        No files found.<br />
        Please upload some files.
      </div>
    )
  }

  renderFile = (file) => {
    const isSelected = this.context.current.name === file;

    return (
      <button
        key={file}
        title={file}
        className={classnames(styles.selectButton, { [styles.selectedFile]: isSelected })}
        onClick={this.onSelect}
      >
        <img className={styles.selectImage} src={`http://localhost:3001/file/${file}`} alt={file} />
        <span className={styles.selectName}>{file}</span>
      </button>
    );
  }

  onSelect = (ev) => this.context.setCurrentFile(ev.currentTarget.title)

  onUpload = async (evt) => {
    const photo = evt.target.files[0];
    const formData = new FormData();
    formData.append("newFile", photo);

    await fetch("http://localhost:3001/upload", { method: "POST", body: formData });

    const response = await fetch("http://localhost:3001/files");
    const json = await response.json();

    this.context.updateFiles(json.files);
  }
}
