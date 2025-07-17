
import { ref, set, get } from 'firebase/database';
import { realtimeDB } from './firebase';

export const writeUserData = async (userId: string, userData: any) => {
  try {
    await set(ref(realtimeDB, `users/${userId}`), userData);
    console.log('User data written successfully');
    return true;
  } catch (error) {
    console.error('Error writing user data:', error);
    return false;
  }
};

export const readUserData = async (userId: string) => {
  try {
    const snapshot = await get(ref(realtimeDB, `users/${userId}`));
    if (snapshot.exists()) {
      console.log('User data:', snapshot.val());
      return snapshot.val();
    } else {
      console.log('No data available');
      return null;
    }
  } catch (error) {
    console.error('Error reading user data:', error);
    return null;
  }
};

//
