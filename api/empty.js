export default function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "https://www.yuvasaathi.in");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type,Authorization");
  res.status(200).end();
}
