import PropTypes from "prop-types";
import React, { Component } from "react";

import styles from "./group.module.css";


export default class Group extends Component {
  static propTypes = {
    data: PropTypes.object,
    isHidden: PropTypes.bool,
    onChange: PropTypes.func,
    onToggleDisplay: PropTypes.func,
  }

  static defaultProps = {
    data: {},
    isHidden: false,
    onChange: () => undefined,
    onToggleDisplay: () => undefined,
  }

  render() {
    const { data, isHidden, onToggleDisplay } = this.props;
    const { name, colonies } = data || {};

    return (
      <div className={styles.container}>
        <div className={styles.controls}>
          <input type="text" placeholder={name} onBlur={this.onChange}/>
          <button className={styles.hideButton} onClick={onToggleDisplay}>
            { isHidden ? "Show" : "Hide" }
          </button>
        </div>
        Count: {colonies.length}
      </div>
    );
  }

  onChange = (evt) => {
    this.props.onChange({
      ...this.props.data,
      name: evt.currentTarget.value || evt.currentTarget.placeholder
    });
  }
}
