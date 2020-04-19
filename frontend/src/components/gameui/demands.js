import React from "react"
import DemandCard from "./demandcard"
import * as gamestate from "../../gamestate"
import * as gameapi from "../../gameapi"

const DemandCards = (props) => {
  const actions = props.actions
  const playerId = props.playerId
  const gameId = props.gameId
  const highlightCity = props.highlightCity
  const setHighlightCity = props.setHighlightCity
  const highlightGood = props.highlightGood
  const setHighlightGood = props.setHighlightGood

  const demandCards = gamestate.demandCardsForPlayer(actions, playerId)
  const fillable = gamestate.demandsFillable(actions, playerId)

  const isBeginningOfTurn = gamestate.isBeginningOfTurn(actions)
  const isYourTurn = gamestate.currentTurn(actions, playerId)
  const canDiscardCards = isBeginningOfTurn && isYourTurn && demandCards.length === 3

  return <div style={{ backgroundColor: "#ddd", padding: "5px" }}>
    <h4>Demand Cards </h4>
    <button disabled={highlightGood == null && highlightCity == null} onClick={() =>{setHighlightGood(null); setHighlightCity(null)}}>Clear Highlights</button>
    <button disabled={demandCards.length >= 3} style={{marginRight: "3px", marginLeft:"3px"}} onClick={() => {gameapi.drawDemandCard(gameId)}}>Draw One</button>
    <button disabled={!canDiscardCards} style={{marginRight: "3px", marginLeft:"3px"}} onClick={() => {gameapi.discardAllDemands(gameId)}}>Discard All</button>
    <div>
      {demandCards.map((demandCard, index) => {
        return <DemandCard highlightGood={highlightGood} highlightCity={highlightCity} setHighlightCity={setHighlightCity} setHighlightGood={setHighlightGood} key={index} card={demandCard} fillable={fillable} fillAction={(good) => {
            fetch(`/game/${gameId}/actions/good/deliver/${good}/card/${demandCard.id}/`, { method: "POST" })
          }
        }/>
      })}
    </div>
  </div>
}

export default DemandCards