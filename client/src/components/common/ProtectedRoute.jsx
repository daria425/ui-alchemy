import { AuthContext } from "../../contexts/AuthContext";
import { useContext, useEffect } from "react";
import { useNavigate, Outlet, useLocation } from "react-router";
export default function ProtectedRoute() {
  const { authenticatedUser, isLoading, error, getIdToken, setError } =
    useContext(AuthContext);
  const location = useLocation();
  const nav = useNavigate();
  console.log("Protected route rerendered with", authenticatedUser);
  useEffect(() => {
    if (error) {
      setError(null);
    }
  }, [location, error, setError]);

  useEffect(() => {
    if (!isLoading) {
      if (error) {
        nav("/403");
      } else if (!authenticatedUser) {
        nav("/login");
      }
    }
  }, [nav, authenticatedUser, error, isLoading]);
  if (isLoading) {
    return null;
  }
  return <Outlet context={{ authenticatedUser, getIdToken }} />;
}
