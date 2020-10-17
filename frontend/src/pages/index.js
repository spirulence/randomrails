import React, { useEffect, useState } from "react"

import Layout from "../components/layout"
import Welcome from "../components/welcome"
import Lobby from "../components/lobby"
import NotPartOfThisGame from "../components/lobby/notpartofthisgame"
import Game from "../components/game"
import base64 from "react-native-base64"


const IndexPage = () => {

  const [gameId, setGameId] = useState(null)
  const [gameMembership, setGameMembership] = useState("unknown")

  useEffect(() => {
    const gameId = new URLSearchParams(window.location.search).get("game_id")
    if (gameId !== null) {
      setGameId(gameId)
      fetch(`/game/${gameId}/my-membership/`)
        .then(response => response.json())
        .then(data => {
          if (data.result === "in_lobby") {
            setGameMembership("in_lobby")
          } else if (data.result === "joined_game") {
            setGameMembership("joined_game")
          } else if (data.result === "not_a_member") {
            setGameMembership("not_a_member")
          }
        })
    }
  }, [])

  function join(color, username){
    fetch(`/game/${gameId}/join/${base64.encode(color)}/${username}/`, {method: "POST"})
      .then(() => {
        fetch(`/game/${gameId}/my-membership/`)
          .then(response => response.json())
          .then(data => {
            if (data.result === "in_lobby") {
              setGameMembership("in_lobby")
            } else if (data.result === "joined_game") {
              setGameMembership("joined_game")
            } else if (data.result === "not_a_member") {
              setGameMembership("not_a_member")
            }
          })
      })
  }

  let mainComponent = <Welcome/>
  if (gameMembership === "in_lobby") {
    mainComponent = <Lobby gameId={gameId} join={join}/>
  } else if (gameMembership === "joined_game") {
    mainComponent = <Game gameId={gameId}/>
  } else if (gameMembership === "not_a_member") {
    mainComponent = <NotPartOfThisGame/>
  }

  return (
    <Layout>
      {mainComponent}
    </Layout>
  )
}

export default IndexPage
