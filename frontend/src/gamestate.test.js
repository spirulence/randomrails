import {trainLocations} from "./gamestate"
import {result as onePlayerGame} from "./testGames/onePlayer"

describe("trainLocations", () => {
  it("returns the correct location", () => {
    expect(trainLocations(onePlayerGame)).toEqual({1:[40, 18]})
  })
})