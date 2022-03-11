import React, { Component } from "react";

import state from "../state";
import Group from "./group";

import styles from "./groups.module.css";

export default class Groups extends Component {
  static contextType = state;

  componentDidMount = async () => {
    const response = await fetch(`http://localhost:3001/file/${this.context.current.name}.json`);
    const json = await response.json();

    const groups = json && json.groups ? json.groups : [];

    this.context.loadGroups(groups)
  }

  render() {
    return (
      <div className={styles.container}>
        <button className={styles.saveButton} onClick={this.onAddNew}>
          Save found colonies
        </button>

        {this.context.current.groups.map(this.renderGroup)}
      </div>
    );
  }

  renderGroup = (data, id) => {
    const { hiddenGroups } = this.context.current;
    const isHidden = hiddenGroups.includes(id);

    return (
      <Group
        key={data.name}
        data={data}
        isHidden={isHidden}
        onToggleDisplay={() => this.onToggleDisplay(id)}
        onChange={(newData) => this.onChange(id, newData)}
      />
    );
  }

  onAddNew = () => {
    const { groups, colonies } = this.context.current;

    const newGroup = {
      name: `Group ${groups.length + 1}`,
      colonies: [...colonies]
    };

    this.context.setColonies(this.context.current.name, []);

    setTimeout(() => this.context.addGroup(newGroup, this.save), 0);
  }

  onChange = (id, data = {}) => {
    this.context.changeGroup(id, data, this.save);
  }

  save = async () => {
    const formData = new FormData();
    formData.append("file", this.context.current.name);
    formData.append("data", JSON.stringify({ groups: this.context.current.groups }));

    await fetch("http://localhost:3001/save", { method: "POST", body: formData });
  }

  onToggleDisplay = (id) => {
    this.context.toggleGroupDisplay(id);
  }
}
