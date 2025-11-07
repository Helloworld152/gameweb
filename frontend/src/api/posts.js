import http from './http'

export const fetchAllPosts = async () => {
  const { data } = await http.get('allposts/')
  return data
}

export const fetchMyPosts = async () => {
  const { data } = await http.get('myposts/')
  return data
}

export const createPost = async payload => {
  const { data } = await http.post('newpost/', payload)
  return data
}

export const deletePost = async postId => {
  await http.delete(`posts/${postId}/`)
}

export const fetchPostDetail = async postId => {
  const { data } = await http.get(`posts/${postId}/`)
  return data
}

export const fetchComments = async postId => {
  const { data } = await http.get(`posts/${postId}/comments/`)
  return data
}

export const addComment = async (postId, payload) => {
  const { data } = await http.post(`posts/${postId}/comments/`, payload)
  return data
}

export const deleteComment = async commentId => {
  await http.delete(`comments/${commentId}/`)
}

