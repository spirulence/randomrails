import React from "react"
import * as gamestate from "../../gamestate"
import { gridToBoardPixelX, gridToBoardPixelY } from "./common"

const TrainsLayer = (props) => {
  const actions = props.actions

  const trainIndicators = {}

  gamestate.ofType(actions, gamestate.types.MOVE_TRAIN).forEach(action => {
    const trainColor = gamestate.colorForPlayer(actions, action.data.playerId)
    const [x, y] = action.data.to

    trainIndicators[action.data.playerId] = <svg key={action.data.playerId} x={gridToBoardPixelX(x, y) - 60}
                                                 y={gridToBoardPixelY(x, y) - 150}>
      <g transform="scale(2,-2) translate(0,-100)" fill={trainColor}>
        <path
          d="M 1.000000 1.500000 L 6.000000 6.500000 L 6.000000 16.500000 L 11.000000 16.500000 L 11.000000 11.500000 L 26.000000 11.500000 L 26.000000 16.500000 L 41.000000 16.500000 L 41.000000 1.500000 L 2.325757 1.500000 Z"
          transform="scale(1.000000,1.000000) translate(4.000000,16.000000)" opacity="1.000000"/>
        <path
          d="M 6.000000 4.000000 C 6.000000 5.380712 4.880712 6.500000 3.500000 6.500000 C 2.119288 6.500000 1.000000 5.380712 1.000000 4.000000 C 1.000000 2.619288 2.119288 1.500000 3.500000 1.500000 C 4.880712 1.500000 6.000000 2.619288 6.000000 4.000000 Z"
          transform="scale(1.000000,1.000000) translate(9.000000,11.000000)" opacity="1.000000"/>
        <path
          d="M 6.000000 4.000000 C 6.000000 5.380712 4.880712 6.500000 3.500000 6.500000 C 2.119288 6.500000 1.000000 5.380712 1.000000 4.000000 C 1.000000 2.619288 2.119288 1.500000 3.500000 1.500000 C 4.880712 1.500000 6.000000 2.619288 6.000000 4.000000 Z"
          transform="scale(1.000000,1.000000) translate(29.000000,11.000000)" opacity="1.000000"/>
        <path
          d="M 6.797190 4.000000 C 6.797190 5.380712 5.677902 6.500000 4.297190 6.500000 C 2.916478 6.500000 1.797190 5.380712 1.797190 4.000000 C 1.797190 2.619288 2.916478 1.500000 4.297190 1.500000 C 5.677902 1.500000 6.797190 2.619288 6.797190 4.000000 Z"
          transform="scale(1.000000,1.000000) translate(34.000000,11.000000)" opacity="1.000000"/>
      </g>
    </svg>
  })

  return (<g>
    {Object.values(trainIndicators)}
  </g>)
}

export default TrainsLayer
