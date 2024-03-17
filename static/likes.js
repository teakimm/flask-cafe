"use strict";
const $likeButton = $(".like");
const $unlikeButton = $(".unlike");
const $likeForm = $("#like-form");
const $unlikeForm = $("#unlike-form");


async function showLikeButton() {
  const cafeId = Number($(".cafe-id").data("cafe-id"));
  const params = new URLSearchParams({"cafe_id" : cafeId});
  const response = await fetch(`/api/likes?${params}`);
  const likeData = await response.json();

  if(!("error" in likeData)) {
    const result = likeData.likes;

    if(result) {
      $unlikeButton.show();
    } else {
      $likeButton.show();
    }

  }
}

async function like(evt) {
  evt.preventDefault();
  const cafeId = Number($(".cafe-id").data("cafe-id"));
  const response = await fetch("/api/like", {
    method: "POST",
    body: JSON.stringify({
      "cafe_id" : cafeId
    }),
    headers: {
      "Content-Type": "application/json"
    }
  });

  const result = await response.json();

  if(!("error" in result)) {
      $unlikeButton.show();
      $likeButton.hide();
  }
}

async function unlike(evt) {
  evt.preventDefault();
  const cafeId = Number($(".cafe-id").data("cafe-id"));
  const response = await fetch("/api/unlike", {
    method: "POST",
    body: JSON.stringify({
      "cafe_id" : cafeId
    }),
    headers: {
      "Content-Type": "application/json"
    }
  });

  const result = await response.json();

  if(!("error" in result)) {
      $likeButton.show();
      $unlikeButton.hide();
  }
}

$likeForm.on("submit", like)
$unlikeForm.on("submit", unlike)

//Render the like/unlike button only when the form exists on the page
if($likeForm.length > 0) {
  showLikeButton()
}
