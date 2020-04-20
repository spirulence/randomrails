import React from "react"
import * as gamestate from "../../gamestate"
import { gridToBoardPixelX, gridToBoardPixelY } from "./common"
import { currentPlayers } from "../../gamestate"

function addTrack(collection, action, colors) {
  const [[x1, y1], [x2, y2]] = [action.data.from, action.data.to]

  collection.unshift(<line
    key={action.sequenceNumber}
    x1={gridToBoardPixelX(x1, y1)} y1={gridToBoardPixelY(x1, y1)}
    x2={gridToBoardPixelX(x2, y2)} y2={gridToBoardPixelY(x2, y2)}
    style={{ stroke: colors[action.data.playerId], strokeWidth: 4 }}
  />)
}

const TrackLayer = (props) => {
  const actions = props.actions
  const playerColors = {}
  Object.values(currentPlayers(actions)).forEach((player) => {
    playerColors[player.playerId] = player.color
  })

  const trackStatus = {}

  gamestate.ofMultipleTypes(actions, [gamestate.types.ADD_TRACK, gamestate.types.ERASE_TRACK]).forEach(action => {
    const [[x1, y1], [x2, y2]] = [action.data.from, action.data.to]
    if (action.type === gamestate.types.ADD_TRACK) {
      trackStatus[`${x1},${y1},${x2},${y2}`] = action
    } else if (action.type === gamestate.types.ERASE_TRACK) {
      trackStatus[`${x1},${y1},${x2},${y2}`] = undefined
    }
  })

  const trackSegments = []
  Object.values(trackStatus)
    .filter(action => action !== undefined)
    .forEach(action => {
      addTrack(trackSegments, action, playerColors)
    })

  return (<g>
    {trackSegments}
  </g>)
}

export default TrackLayer
