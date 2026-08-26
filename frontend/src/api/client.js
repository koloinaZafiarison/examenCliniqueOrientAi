import axios from "axios";

export async function orient(responses) { return (await axios.post("http://localhost:8000/api/orient", { responses })).data; }