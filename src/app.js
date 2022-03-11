import React, { Component } from "react";

import styles from "./app.module.css";
import Navigation from "./navigation";
import Controls from "./controls";
import View from "./view"
import state from "./state";


export default class App extends Component {
  constructor(...args) {
    super(...args);

    this.state = {
      current: {
        name: undefined,
        colonies: [],
        groups: [],
        zoom: {},
        loading: false,
        displayColonies: true,
        hiddenGroups: []
      },
      files: [],
      updateFiles: this.onUpdateFiles,
      setCurrentFile: this.onSetCurrent,
      setColonies: this.onSetColonies,
      setZoom: this.onZoomChange,
      toggleDisplay: this.onToggleDisplay,
      loadGroups: this.onLoadGroups,
      addGroup: this.onAddGroup,
      changeGroup: this.onChangeGroup,
      toggleGroupDisplay: this.onToggleGroupDisplay,
    };
  }

  render() {
    return (
      <state.Provider value={this.state}>
        <div className={styles.app}>
          <Navigation />
          <View />
          <Controls key={this.state.current.name} />
        </div>
      </state.Provider>
    );
  }

  onUpdateFiles = (files) => {
    this.setState({ files: files });
  }

  onSetCurrent = (file) => {
    this.setState({
      current: {
        name: file,
        colonies: [],
        zoom: {},
        groups: [],
        displayColonies: true,
        hiddenGroups: []
      }
    });
  }

  onSetColonies = (file, data) => {
    if (this.state.current.name !== file) {
      return;
    }

    this.setState({
      current: {
        ...this.state.current,
        colonies: data
      }
    });
  }

  onZoomChange = (level = 0.25, isDefault = false) => {
    this.setState({
      current: {
        ...this.state.current,
        zoom: {
          level,
          default: isDefault ? level : this.state.current.zoom.default
        }
      }
    });
  }

  onToggleDisplay = () => {
    this.setState({
      current: {
        ...this.state.current,
        displayColonies: !this.state.current.displayColonies
      }
    });
  }

  onLoadGroups = (data) => {
    this.setState({
      current: {
        ...this.state.current,
        groups: data
      }
    });
  }

  onAddGroup = (newGroup, callback) => {
    const { groups } = this.state.current;

    this.setState({
      current: {
        ...this.state.current,
        groups: [newGroup, ...groups]
      }
    }, callback);
  }

  onChangeGroup = (id, data, callback) => {
    const groups = this.state.current.groups.map((group, i) => {
      if ( i !== id ) {
        return {...group};
      }

      return {...group, ...data};
    });

    this.setState({
      current: {
        ...this.state.current,
        groups: groups
      }
    }, callback);
  }

  onToggleGroupDisplay = (id) => {
    const {hiddenGroups} = this.state.current;

    if (hiddenGroups.includes(id)) {
      this.setState({
        current: {
          ...this.state.current,
          hiddenGroups: [...hiddenGroups.filter((i) => i !== id)]
        }
      });
    } else {
      this.setState({
        current: {
          ...this.state.current,
          hiddenGroups: [...hiddenGroups, id]
        }
      });
    }
  }
}
