import React from "react"
import { gridToBoardPixelX, gridToBoardPixelY } from "./common"
import { ofType, types } from "../../gamestate"

const CountriesLayer = (props) => {
  const citiesElements = []

  ofType(props.actions, types.ADD_COUNTRY).forEach(action => {
    const [x, y] = action.data.labelPoint

    const name = action.data.name
    citiesElements.push(<text style={{ font: "80px sans-serif", userSelect: "none", fill: "#ddd", stroke: "black", strokeWidth: "2px", opacity: "0.4" }}
                              x={gridToBoardPixelX(x, y)}
                              y={gridToBoardPixelY(x, y)} textAnchor={"middle"} >{name}</text>,
    )
  })

  return (
    <g>
      {citiesElements}
    </g>
  )
}

export default CountriesLayer