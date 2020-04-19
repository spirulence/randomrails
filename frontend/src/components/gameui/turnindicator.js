import React, { useEffect } from "react"
import * as gamestate from "../../gamestate"
import * as gameapi from "../../gameapi"

const TurnIndicator = (props) => {
  const actions = props.actions
  const gameId = props.gameId
  const playerId = props.playerId

  const currentTurn = gamestate.currentTurn(actions, playerId)
  const isStarted = gamestate.gameIsStarted(actions);

  const players = Object.values(gamestate.currentPlayers(actions))
  players.sort(p => p.playOrder)

  const currentPlayer = players[currentTurn.playOrder]
  const currentColor = currentPlayer !== undefined ? currentPlayer.color : "#000"

  const whoseTurn = <h4>It is <div style={{
    display: "inline-block",
    backgroundColor: currentColor,
    width: "30px",
    height: "30px",
    marginRight: "5px",
  }}/> turn.</h4>

  const yourTurn = <div>
    <h2>Your Turn!</h2>
    <h4>Moved Train {gamestate.trainMovementThisTurn(actions)}/12</h4>
    <h4>Built Track 0/25</h4>
    <button onClick={() => {gameapi.advanceTurn(gameId)}}>End Turn</button>
  </div>

  const otherTurn = <div>
    {whoseTurn}
  </div>

  const notStarted = <div>
    <h3>Game has not started</h3>
  </div>

  if (!isStarted){
    return notStarted
  }else if (currentTurn.isYou){
    return yourTurn
  }else{
    return otherTurn
  }
}

export default TurnIndicator