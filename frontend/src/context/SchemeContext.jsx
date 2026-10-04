import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchSavedSchemes, saveSchemeApi, deleteSavedSchemeApi } from '../services/api';

const SchemeContext = createContext();

export const SchemeProvider = ({ children }) => {
  const [savedSchemes, setSavedSchemes] = useState([]);
  const [compareIds, setCompareIds] = useState([]);
  const [userProfile, setUserProfile] = useState({
    state: 'Tamil Nadu',
    category: 'SC',
    annual_income: 250000,
    occupation: 'Student',
    education_level: 'Undergraduate',
  });
  const [loadingSaved, setLoadingSaved] = useState(false);

  const loadSavedSchemes = async () => {
    try {
      setLoadingSaved(true);
      const data = await fetchSavedSchemes();
      setSavedSchemes(data);
    } catch (err) {
      console.warn("Could not load saved schemes from backend API yet:", err);
    } finally {
      setLoadingSaved(false);
    }
  };

  useEffect(() => {
    loadSavedSchemes();
  }, []);

  const toggleSaveScheme = async (schemeId) => {
    const isAlreadySaved = savedSchemes.some((s) => s.scheme_id === schemeId);
    if (isAlreadySaved) {
      const match = savedSchemes.find((s) => s.scheme_id === schemeId);
      if (match) {
        try {
          await deleteSavedSchemeApi(match.id);
          setSavedSchemes((prev) => prev.filter((s) => s.id !== match.id));
        } catch (err) {
          console.error("Failed to delete saved scheme", err);
        }
      }
    } else {
      try {
        const res = await saveSchemeApi(schemeId);
        await loadSavedSchemes();
      } catch (err) {
        console.error("Failed to save scheme", err);
      }
    }
  };

  const toggleCompareScheme = (schemeId) => {
    setCompareIds((prev) => {
      if (prev.includes(schemeId)) {
        return prev.filter((id) => id !== schemeId);
      } else {
        if (prev.length >= 4) {
          alert("You can compare up to 4 schemes at a time.");
          return prev;
        }
        return [...prev, schemeId];
      }
    });
  };

  return (
    <SchemeContext.Provider
      value={{
        savedSchemes,
        loadSavedSchemes,
        toggleSaveScheme,
        compareIds,
        setCompareIds,
        toggleCompareScheme,
        userProfile,
        setUserProfile,
        loadingSaved,
      }}
    >
      {children}
    </SchemeContext.Provider>
  );
};

export const useSchemeContext = () => useContext(SchemeContext);
