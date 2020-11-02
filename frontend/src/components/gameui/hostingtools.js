import React, { useEffect, useState } from "react"
import * as gameapi from "../../gameapi"
import * as gamestate from "../../gamestate"
import { createInviteCode } from "../../gameapi"
import { gameIsStarted } from "../../gamestate"

const HostingTools = (props) => {
  const gameId = props.gameId
  const actions = props.actions

  const [joincodePrefix, setJoincodePrefix] = useState("")
  const [joincode, setJoincode] = useState("")

  useEffect(() => {
    createInviteCode(gameId, setJoincode)

    const interval = setInterval(() => {
      createInviteCode(gameId, setJoincode)
    }, 60000 * 4.5)
    return function() {
      clearInterval(interval)
    }
  }, [gameId])

  function moneyButtons(playerId) {
    return [-50, -10, -5, -1, 1, 5, 10, 50].map((amount) => (<button key={amount} onClick={() => {
      gameapi.adjustMoney(gameId, playerId, amount)
    }
    }>${amount}M</button>))
  }

  function copyInviteLinkButon(){
    return <button onClick={() => {
        const fullInviteUrl = window.location.protocol + "//" + window.location.host + `/game/${gameId}/invite/use/${joincode}`
        navigator.clipboard.writeText(fullInviteUrl).then(() => {alert("invite code copied")});
      }}>Copy Invite Code</button>
  }

  function copyRejoinCodeButton(playerId){
    return <button onClick={() => {
      gameapi.createRejoinCode(gameId, playerId).then(code => {
        const fullRejoinUrl = window.location.protocol + "//" + window.location.host + `/game/${gameId}/rejoin/use/${code}`
        navigator.clipboard.writeText(fullRejoinUrl).then(() => {alert("rejoin code copied")});
      })
    }}>Copy Rejoin Code</button>
  }

  const players = Object.values(gamestate.currentPlayers(actions))
  players.sort(p => p.playOrder)

  const playersHtml = players.map((player, index) => {
      return <div key={index} >
        <p><div style={{
          display: "inline-block",
          backgroundColor: player.color,
          width: "30px",
          height: "30px",
          marginRight: "5px",
        }}/>{moneyButtons(player.playerId)}{copyRejoinCodeButton(player.playerId)}</p>
      </div>
    })



  return (
    <div style={{ display: props.show ? "block" : "none", backgroundColor: "#ddd", borderTop:"black solid 10px" }}>
      <h5>Hosting Tools</h5>
      {
      gameIsStarted(actions) ? 
        <></> : 
        <div>
          <button onClick={() => {gameapi.startGame(gameId)}}>Start Game</button>
          <p>Invite others! {copyInviteLinkButon()}</p>
        </div>
      }
        {playersHtml}
    </div>
  )
}

export default HostingTools