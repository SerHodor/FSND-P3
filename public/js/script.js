$(document).ready(function() {
    jQuery.each(jQuery('textarea[data-autoresize]'), function() {

        var resizeTextarea = function(el) {
            jQuery(el).css('height', 'auto').css('height', el.scrollHeight);
        };
        jQuery(this).on('keyup input', function() { resizeTextarea(this); }).removeAttr('data-autoresize');
    });
});

function toggleHidden(event) {
    var selector = $(event.target).parent().children(".comment-box");
    selector.toggleClass("hidden");
    if (!selector.hasClass("hidden")) {
        selector.find(".comment-button").trigger("click");
    }
}

function Blogresponse(blog_id, toDo, callback, content = "") {
    var data = {};
    data.toDo = toDo;
    data.content = content;
    $.ajax({
        url: "/" + blog_id + "/UserResponse",
        type: "POST",
        data: data,
        success: function(data) {
            callback(data);
        },
        error: function(error) {
            callback("Something went wrong.");
        }
    });
}

function Like(event, blog_id) {

    var toDo = "Like";
    Blogresponse(blog_id, toDo, function(data) {
        if (data) {
            $(".warning").removeClass("hidden");
            var warning = "<strong>Warning!</strong> " + data;
            $(".warning").html(warning);
            console.log(data);
        } else {

            $(event.target).toggleClass("text-success");
            var score_select = $(event.target).parent().children("div").eq(1);
            var x = score_select.html();
            x = parseInt(x);
            var unlike_select = $(event.target).parent().children("div").eq(2);
            if (unlike_select.hasClass("text-danger")) {
                unlike_select.toggleClass("text-danger");
                x += 1;
            }

            if ($(event.target).hasClass("text-success")) {
                x += 1;
            } else {
                x -= 1;
            }
            x = x.toString();
            score_select.html(x);
        }
    });
}

function Unlike(event, blog_id) {

    var toDo = "DisLike";
    Blogresponse(blog_id, toDo, function(data) {

        if (data) {
            $(".warning").removeClass("hidden");
            var warning = "<strong>Warning!</strong> " + data;
            $(".warning").html(warning);
            console.log(data);
        } else {

            $(event.target).toggleClass("text-danger");
            var score_select = $(event.target).parent().children("div").eq(1);
            var x = score_select.html();
            x = parseInt(x);
            var like_select = $(event.target).parent().children("div").eq(0);
            if (like_select.hasClass("text-success")) {
                like_select.toggleClass("text-success");
                x -= 1;
            }

            if ($(event.target).hasClass("text-danger")) {
                x -= 1;
            } else {
                x += 1;
            }
            x = x.toString();
            score_select.html(x);
        }
    });
}

function Comment(event, blog_id) {

    var toDo = "Comment";
    var textarea_select = $(event.target).parent().parent().children("textarea");
    var display_comments = $(event.target).closest(".comment-box").find(".display-comments");

    var content = textarea_select.val();
    textarea_select.val('');
    var username;
    try {
        username = document.cookie;
        username = username.split(";")[0].split("=")[1];
    } catch (error) {}
    if ((!username) && content) {
        $(".warning-display").html("Please log in to make comment");
        $(".warning-display").removeClass("hidden");
        return;
    }
    Blogresponse(blog_id, toDo, function(data) {
        try {
            if (data) {
                data = JSON.parse(data);
                if (data.length > 0) {
                    var display = "";
                    var username = document.cookie;
                    username = username.split("|")[0].split("=")[1];
                    var edit = "";
                    for (var i = data.length - 1; i >= 0; i--) {
                        edit = "";
                        if (username && username == data[i].created_by) {
                            edit = '<a class="text-muted clickable pull-right" data-toggle="modal" data-target="#' + "commentDelete" + data[i].comment_id + '">&nbsp;del</a><a class="text-muted clickable pull-right" data-toggle="modal" data-target="#' + "commentEdit" + data[i].comment_id + '">edit</a>';
                            edit += '<div class="modal fade" id="' + "commentEdit" + data[i].comment_id + '" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button><h4 class="modal-title" id="myModalLabel">Edit Comment</h4></div><div class="modal-body"><textarea>' + data[i].content + '</textarea></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close</button><button type="button" class="btn btn-primary" onclick="editcomment(event,' + data[i].comment_id + ')">Make changes</button></div></div></div></div>';
                            edit += '<div class="modal fade" id="' + "commentDelete" + data[i].comment_id + '" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button><h4 class="modal-title" id="myModalLabel">Delete Comment</h4></div><div class="modal-body">Are you sure you want to delete this comment?</div><div class="modal-footer"><button type="button" class="btn btn-primary" data-dismiss="modal">No</button><button type="button" class="btn btn-default" onclick="deletecomment(event,' + data[i].comment_id + ')">Yes</button></div></div></div></div>';
                        }
                        display += '<div class="comment"><strong>' + data[i].created_by + ' </strong>' + edit + '<br><div class="content">' + data[i].content + '</div></div>';
                    }
                } else {
                    display = '<div class="comment"><em>No comments to show.</em></div>';
                }
                display_comments.html(display);
            }
        } catch (err) {}

    }, content);

}

function editcomment(event, comment_id) {
    var data = {};
    var textarea_value = $(event.target).closest(".modal").find("textarea").val();
    data.content = textarea_value;
    $.ajax({
        url: "/comments/edit/" + comment_id,
        type: "POST",
        data: data,
        success: function(data) {
            if (data == "success") {
                $(event.target).closest(".comment").children(".content").html('<strong>' + textarea_value + '</strong>');
                $("#" + "commentEdit" + comment_id).modal('hide');
            } else {
                $("#" + "commentEdit" + comment_id).modal('hide');
                console.log(data);
            }
        },
        error: function(error) {
            $("#" + "commentEdit" + comment_id).modal('hide');
            console.log("Something went wrong.");
        }
    });
}

function deletecomment(event, comment_id) {
    $.ajax({
        url: "/comments/delete/" + comment_id,
        type: "POST",
        data: "",
        success: function(data) {
            if (data == "success") {
                $(event.target).closest(".comment").children(".content").html("<em>this comment has been deleted</em>");
                $(event.target).closest(".comment").children("a").addClass("hide");
                $("#" + "commentDelete" + comment_id).modal('hide');
            } else {
                $("#" + "commentDelete" + comment_id).modal('hide');
                console.log(data);
            }
        },
        error: function(error) {
            $("#" + "commentDelete" + comment_id).modal('hide');
            console.log("Something went wrong.");
        }
    });
}

function DeleteBlog(event, blog_id) {
    $.ajax({
        url: "/" + blog_id + "/DeleteBlog",
        type: "POST",
        success: function(data) {
            if (data == "success") {
                $(event.target).closest(".blog").children(".text-justify").eq(0).html("<em>This post has been deleted.</em>");
                $("#" + blog_id).modal('hide');
            } else {
                $(".warning").removeClass("hidden");
                var warning = "<strong>Warning!</strong> " + data;
                $(".warning").html(warning);
                $("#" + blog_id).modal('hide');
                console.log(data);
            }
        },
        error: function(error) {
            console.log("Something went wrong.");
        }
    });
}
