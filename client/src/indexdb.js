// src/utils/indexeddb.js

const dbName = 'RestaurantDB';
const storeName = 'restaurants';

function openDB() {
	return new Promise((resolve, reject) => {
		const request = indexedDB.open(dbName, 1);

		request.onupgradeneeded = (event) => {
			const db = event.target.result;
			if (!db.objectStoreNames.contains(storeName)) {
				db.createObjectStore(storeName, { keyPath: 'id' });
			}
		};

		request.onsuccess = (event) => {
			resolve(event.target.result);
		};

		request.onerror = (event) => {
			reject(event.target.error);
		};
	});
}

export function saveData(data) {
	return openDB().then((db) => {
		return new Promise((resolve, reject) => {
			const transaction = db.transaction(storeName, 'readwrite');
			const store = transaction.objectStore(storeName);

			data.forEach((item) => store.put(item));

			transaction.oncomplete = () => resolve();
			transaction.onerror = (event) => reject(event.target.error);
		});
	});
}

export function getData() {
	return openDB().then((db) => {
		return new Promise((resolve, reject) => {
			const transaction = db.transaction(storeName, 'readonly');
			const store = transaction.objectStore(storeName);

			const request = store.getAll();
			request.onsuccess = (event) => resolve(event.target.result);
			request.onerror = (event) => reject(event.target.error);
		});
	});
}
