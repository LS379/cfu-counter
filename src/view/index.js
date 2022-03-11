import React, { Component } from "react";

import state from "../state";
import AlogrithmStageSelector from "./algorithmStages";
import Loading from "./layers/loading";
import MarkersLayer from "./layers/markers";
import ImageLayer from "./layers/image";
import styles from "./index.module.css";


export default class View extends Component {
  static contextType = state;

  state = {
    loading: false,
    name: undefined,
    stages: {},
    currentStage: undefined,
    naturalWidth: 0,
    naturalHeight: 0,
  };

  componentDidUpdate() {
    const { name } = this.context.current;
    if(this.state.name === name) {
      return;
    }

    this.setState({
      loading: true,
      name,
      naturalWidth: 0,
      naturalHeight: 0,
      stages: {},
      currentStage: undefined,
    });

    const img = new Image();

    img.addEventListener("load", this.onImageLoad)
    img.src = `http://localhost:3001/file/${name}`;
  }

  render() {
    const loading = this.state.loading || this.context.current.loading;

    return (
      <div ref={this.setContainer} className={styles.container}>
        <AlogrithmStageSelector
          values={Object.keys(this.state.stages)}
          current={this.state.currentStage}
          onChange={this.onStageChange}
        />

        {this.renderLayers()}
        <Loading isLoading={loading} />
      </div>
    )
  }

  renderLayers() {
    const { name, naturalWidth, naturalHeight } = this.state;

    if(!name) {
      return (
        <div className={styles.message}>
          No file selected. <br/>
          Please select a file.
        </div>
      );
    }

    let img = `http://localhost:3001/file/${name}`;
    if(this.state.currentStage) {
      img = this.state.stages[this.state.currentStage];
    }

    const colonies = this.context.current.colonies || [];
    const { displayColonies } = this.context.current;
    const { level: zoomLevel } = this.context.current.zoom;

    const width = (naturalWidth * zoomLevel) || 0;
    const height = (naturalHeight * zoomLevel) || 0;

    const markers = colonies.map(([x, y]) => [Math.ceil(x * zoomLevel), Math.ceil(y * zoomLevel)]);

    return (
      <div className={styles.colonyContainer}>
        <div style={{ width, height }} onClick={this.onSelect} >
          <ImageLayer src={img} width={width} height={height} />
          <MarkersLayer markers={markers} colorSeed="original" isVisible={displayColonies}/>

          {this.context.current.groups.map(this.renderGroupMarkers)}
        </div>
      </div>
    );
  }

  renderGroupMarkers = (data, id) => {
    const { displayColonies, hiddenGroups } = this.context.current;
    const isVisible = displayColonies && !hiddenGroups.includes(id);

    const { level: zoomLevel } = this.context.current.zoom;
    const { colonies, name } = data;
    const markers = colonies.map(([x, y]) => [Math.ceil(x * zoomLevel), Math.ceil(y * zoomLevel)]);

    return <MarkersLayer key={`${name}_${id}`} markers={markers} colorSeed={id} isVisible={isVisible} />
  }

  containerNode = null;
  setContainer = (node) => this.containerNode = node

  onImageLoad = (evt) => {
    const { width, height } = evt.currentTarget;

    const { width: containerWidth, height: containerHeight } = this.containerNode.getBoundingClientRect();

    const containerRatio = Math.ceil(containerWidth / containerHeight * 100) / 100;
    const ratio = Math.ceil(width / height * 100) / 100;

    const threshold = 120;
    let zoomLevel = undefined;

    if(ratio <= containerRatio) {
      zoomLevel = Math.ceil((containerHeight - threshold) / height * 100) / 100;
    } else {
      zoomLevel = Math.ceil((containerWidth - threshold) / width* 100) / 100;
    }

    this.context.setZoom(zoomLevel, true);

    this.setState({ naturalWidth: width, naturalHeight: height, loading: false });
  }

  onSelect = async (evt) => {
    this.setState({ loading: true });

    const {left, top, width, height} = evt.currentTarget.getBoundingClientRect();
    const x = evt.clientX - left;
    const y = evt.clientY - top;

    const { naturalWidth, naturalHeight } = this.state;

    const scaledX = Math.ceil(x * naturalWidth / width);
    const scaledY = Math.ceil(y * naturalHeight / height);

    const file = this.context.current.name;
    const response = await fetch(`http://localhost:3001/colonies?file=${file}&x=${scaledX}&y=${scaledY}`);

    const json = await response.json();

    if (json) {
      this.context.setColonies(file, JSON.parse(json)["circles"][0] || []);
      this.setState({stages: JSON.parse(json).stages, loading: false});
    }
    else {
      this.setState({stages: {}, loading: false});
    }
  }

  onStageChange = (name) => this.setState({ currentStage: name });
}
