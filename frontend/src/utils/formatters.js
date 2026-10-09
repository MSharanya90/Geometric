export const formatBytes = (bytes, decimals = 1) => {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '—';
  return Number(num).toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: decimals,
  });
};

export const formatArea = (area_m2) => {
  if (area_m2 === null || area_m2 === undefined) return '—';
  const m2 = formatNumber(area_m2, 2);
  const ha = (area_m2 / 10000).toFixed(2);
  return `${m2} m² (${ha} ha)`;
};

export const formatLength = (length_m) => {
  if (length_m === null || length_m === undefined) return '—';
  const m = formatNumber(length_m, 2);
  const km = (length_m / 1000).toFixed(2);
  return `${m} m (${km} km)`;
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
};
