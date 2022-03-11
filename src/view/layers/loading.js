import PropTypes from "prop-types";
import React, { Component } from "react";

import styles from "./loading.module.css";

export default class Loading extends Component {
  static propTypes = {
    isLoading: PropTypes.bool
  }

  static defaultProps = {
    isLoading: false
  }

  render() {
    const { isLoading } = this.props;
    if(!isLoading) {
      return null;
    }

    return (
      <div className={styles.container}>
        <div className={styles.spinner} />
      </div>
    );
  }
}
