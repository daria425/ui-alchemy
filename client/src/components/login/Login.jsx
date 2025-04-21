import { useReducer, useContext } from "react";
import { useNavigate } from "react-router";
import { AuthContext } from "../../contexts/AuthContext";
const initialState = {
  email: "",
  password: "",
};

function formReducer(state, action) {
  switch (action.type) {
    case "USER_INPUT":
      return {
        ...state,
        [action.field]: action.payload,
      };
  }
}

export default function Login() {
  const [state, dispatch] = useReducer(formReducer, initialState);
  const { login, loginWithGoogle } = useContext(AuthContext);
  const nav = useNavigate();
  const handleInputChange = (e) => {
    dispatch({
      type: "USER_INPUT",
      field: e.target.name,
      payload: e.target.value,
    });
  };

  const handleLogin = async (e, provider) => {
    e.preventDefault();
    try {
      switch (provider) {
        case "email":
          await login(state.email, state.password);
          break;
        case "google":
          await loginWithGoogle();
          break;
      }
      nav("/app");
    } catch (err) {
      console.error("Signup error", err);
    }
  };
  return (
    <div className="auth">
      <form
        className="auth__form"
        onSubmit={async (e) => {
          handleLogin(e, "email");
        }}
      >
        <h1 className="auth__heading">Log in</h1>
        <div className="auth__field">
          <label htmlFor="email" className="auth__input-label">
            Email:
          </label>
          <input
            required
            type="text"
            id="email"
            name="email"
            value={state.email}
            onChange={(e) => {
              handleInputChange(e);
            }}
            className="auth__input"
          ></input>
        </div>
        <div className="auth__field">
          <label htmlFor="password" className="auth__input-label">
            Password:
          </label>

          <input
            required
            type="password"
            id="password"
            name="password"
            value={state.password}
            className="auth__input"
            onChange={(e) => {
              handleInputChange(e);
            }}
          ></input>
        </div>
        <div className="auth__btn-container">
          <button className="auth__btn" type="submit">
            Log in
          </button>
          <button
            className="auth__btn auth__btn--google"
            type="button"
            onClick={(e) => {
              handleLogin(e, "google");
            }}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              height={"1em"}
              width={"1em"}
            >
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
              <path d="M1 1h22v22H1z" fill="none" />
            </svg>
            Log in with Google
          </button>
        </div>
      </form>
    </div>
  );
}
