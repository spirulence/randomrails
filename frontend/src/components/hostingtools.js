import React, { useEffect, useState } from "react"

const HostingTools = (props) => {
  const [needToFetch, setNeedToFetch] = useState(true)
  const [slots, setSlots] = useState([])
  const [joincodePrefix, setJoincodePrefix] = useState("")
  const gameId = props.gameId;

  useEffect(() => {
    setJoincodePrefix(window.location.protocol + "//" + window.location.host + `/game/${gameId}/join/`)
  },[gameId])

  useEffect(() => {
    if (needToFetch) {
      fetch(`/game/${gameId}/slots`).then(
        (response) => {
          return response.json()
        },
      ).then((data) => {
        setSlots(data.result)
        setNeedToFetch(false)
      })
    }
  }, [needToFetch, gameId])

  const slotHtml = slots.map((slot, index) => {
    return <p key={index}><div style={{ display: "inline-block", backgroundColor: slot.color, width: "30px", height: "30px", marginRight: "5px" }}/>{joincodePrefix + slot.joincode}</p>
  });

  return (
    <div style={{display: props.show ? "block": "none"}}>
      <h5>Hosting Tools</h5>
      {slotHtml}
    </div>
  )
}

export default HostingTools