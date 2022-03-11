import React, { Component } from "react";

import state from "../state";
import Groups from "./groups";
import styles from "./index.module.css";


export default class Controls extends Component {
  static contextType = state;

  state = {};

  render() {
    if(!this.context.current.name) {
      return null;
    }

    let counted = this.context.current.colonies.length;

    let total = counted;
    this.context.current.groups.forEach(({colonies}) => {
      total += colonies.length;
    });

    const { displayColonies } = this.context.current;

    return (
      <div className={styles.container}>
        <div className={styles.fileControls}>
          <button onClick={this.onZoomIn}> + </button>
          <button onClick={this.onZoomOut}> - </button>
          <button onClick={this.onResetZoom}> ↺ </button>
          <button onClick={this.onToggleDisplay}> { displayColonies ? "Hide" : "Show" } </button>
        </div>

        <div className={styles.counter}>
          Last analysis: {counted}
        </div>
        <div className={styles.counter}>
          Total: {total}
        </div>

        <Groups />
      </div>
    );
  }

  onZoomIn = () => {
    const { level } = this.context.current.zoom || {};
    const zoomLevels = this.zoomLevels();
    const pos = zoomLevels.indexOf(level);

    let newLevel = level;

    if(pos !== -1 && pos + 1 < zoomLevels.length) {
      newLevel = zoomLevels[pos + 1];
    }

    this.context.setZoom(newLevel);
  }

  onZoomOut = () => {
    const { level } = this.context.current.zoom || {};
    const zoomLevels = this.zoomLevels();
    const pos = zoomLevels.indexOf(level);

    let newLevel = level;

    if(pos !== -1 && pos - 1 >= 0) {
      newLevel = zoomLevels[pos - 1];
    }

    this.context.setZoom(newLevel);
  }

  onResetZoom = () => {
    const { default: defaultLevel } = this.context.current.zoom;
    this.context.setZoom(defaultLevel);
  }

  onToggleDisplay = () => {
    this.context.toggleDisplay();
  }

  zoomLevels() {
    const { default: defaultLevel } = this.context.current.zoom;
    const levels = [0.15, 0.2, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, defaultLevel];

    return levels.filter((elem, pos) => levels.indexOf(elem) === pos).sort();
  }
}
