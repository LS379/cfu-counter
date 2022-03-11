import classnames from "classnames";
import PropTypes from "prop-types";
import randomcolor from "randomcolor";
import React, { Component } from "react";

import Point from "./point";
import styles from "./markers.module.css";


export default class MarkersLayer extends Component {
  static propTypes = {
    markers: PropTypes.array,
    className: PropTypes.string,
    markerClassName: PropTypes.string,
    colorSeed: PropTypes.any,
    isVsibile: PropTypes.bool,
  }

  static defaultProps = {
    markers: [],
    className: undefined,
    markerClassName: undefined,
    colorSeed: undefined,
    isVisible: true,
  }

  render() {
    const { markers, className, isVisible } = this.props;
    if (!isVisible) {
      return null;
    }


    return (
      <div className={classnames(styles.container, className)}>
        {markers.map(this.renderPoint)}
      </div>
    );
  }

  renderPoint = ([x, y]) => {
    const { markerClassName, colorSeed } = this.props;
    const className = classnames(styles.marker, markerClassName);
    const color = randomcolor({ seed: colorSeed, hue: "random", luminosity: "light"});

    return <Point key={`${x}_${y}`} className={className} style={{ top: y, left: x, fill: color }} />;
  }
}
