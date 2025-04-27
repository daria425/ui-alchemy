import { useContext, useState, useEffect, useCallback } from "react";
import { AuthContext } from "../services/AuthProvider";
import { apiConfig } from "../config/api.config";
import { auth } from "../config/firebase.config";

function useData(urlPath, queryParams) {
  const { authenticatedUser } = useContext(AuthContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState(false);
  const fullUrl = queryParams ? `${urlPath}?${queryParams}` : urlPath;
  const getData = useCallback(async () => {
    try {
      setLoading(true);
      setFetchError(false);
      if (authenticatedUser) {
        const idToken = await auth.currentUser.getIdToken();
        const response = await apiConfig.get(fullUrl, {
          headers: {
            Authorization: `Bearer ${idToken}`,
          },
        });
        if (response.status === 200) {
          setData(response.data);
        } else {
          console.error("Error fetching user data:", response);
          setFetchError({
            message: `Server response failed with status code ${response.status}`,
          });
        }
      }
    } catch (err) {
      console.error("Error fetching user data:", err);
      setFetchError({ message: err.message });
    } finally {
      setLoading(false);
    }
  }, [authenticatedUser, fullUrl]);

  useEffect(() => {
    getData();
  }, [getData]);
  return {
    data,
    setData,
    loading,
    fetchError,
    refetch: getData,
  };
}

export { useData };
