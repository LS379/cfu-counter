import PropTypes from "prop-types";
import React, { Component } from "react";


export default class ImageLayer extends Component {
  static propTypes = {
    src: PropTypes.string,
    width: PropTypes.number,
    height: PropTypes.number,
  }

  static defaultProps = {
    src: "",
    width: 0,
    height: 0,
  }

  render() {
    const { width, height, src } = this.props;

    return (
      <div
        style={{
          backgroundImage: `url(${src})`,
          backgroundSize: "cover",
          backgroundRepeat: "no-repeat",
          width: `${width}px`,
          height: `${height}px`
        }}
      />
    )
  }
}
