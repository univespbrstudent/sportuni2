#Importar bibliotecas
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db

#Criar views
views = Blueprint("views", __name__)

#Criar route para home
@views.route("/")
@views.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user=current_user, posts=posts)

#Criar route para post
@views.route("/create-post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        sport = request.form.get('sport')
        place = request.form.get('place')
        phone = request.form.get('phone')

        if not text:
            flash('Post deve conter um texto válido', category='error')
        else:
            post = Post(text=text, sport=sport,place=place, phone=phone, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post criado! Agora é só esperar alguém entrar em contato com você', category='success')
            return redirect(url_for('views.home'))

    return render_template('create_post.html', user=current_user)

#Criar route para delete do post
@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post não existe.", category='error')
    elif current_user.id != post.id:
        flash('Você não tem permissão para excluir este post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post excluído com sucesso.', category='success')

    return redirect(url_for('views.home'))

#Criar route para username
@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('Não existe username para este usuário.', category='error')
        return redirect(url_for('views.home'))

    posts = user.posts
    return render_template("posts.html", user=current_user, posts=posts, username=username)

#Criar route para comentários
@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comentário não pode ser vazio.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post não existe.', category='error')

    return redirect(url_for('views.home'))

#Criar route para deletar comentário
@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comentário não existe.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('Você não tem permissão para excluir este comentário.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))

#Criar route para like
@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post não existe.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})
