import Redis from "ioredis";

const redis = process.env.REDIS_URL ? new Redis(process.env.REDIS_URL) : null;
const mem = new Map(); // fallback when Redis is not configured

export const get = async (k) => (redis ? redis.get(k) : mem.get(k));
export const set = async (k, v) => (redis ? redis.set(k, v, "EX", 3600) : mem.set(k, v));
