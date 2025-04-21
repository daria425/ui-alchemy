import { useNavigate } from "react-router";
import { useEffect } from "react";
export default function Index() {
  const nav = useNavigate();
  useEffect(() => {
    nav("/login");
  });
}
