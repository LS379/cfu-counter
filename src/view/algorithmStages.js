import PropTypes from "prop-types";
import React, { Component } from "react";

import styles from "./algorithmStages.module.css";


export default class AlgorithmStages extends Component {
  static propTypes = {
    values: PropTypes.array,
    current: PropTypes.string,
    onChange: PropTypes.func,
  }

  static defaultProps = {
    values: {},
    current: undefined,
    onChange: () => undefined,
  }

  render() {
    const { values, current } = this.props;
    if(values.length === 0) {
      return null;
    }

    const isDefaultSelected = !values.includes(current);

    return (
      <div className={styles.container}>
        <button
          className={styles.button}
          onClick={this.onReset}
          aria-selected={isDefaultSelected}
          role="tab"
        >
          ORIGINAL
        </button>

        {values.map(this.renderStageButton)}
      </div>
    );
  }

  renderStageButton = (name) => {
    const { current } = this.props;
    const isSelected = current === name;

    return (
      <button
        key={name}
        className={styles.button}
        onClick={this.onChange}
        aria-selected={isSelected}
        title={name}
        role="tab"
      >
        {name}
      </button>
    )
  }

  onChange = (evt) => this.props.onChange(evt.currentTarget.title);

  onReset = () => this.props.onChange(undefined);
}
