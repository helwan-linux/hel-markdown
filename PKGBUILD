# Maintainer: Said <youremail@example.com>
pkgname=hel-markdown
pkgver=1.0.0
pkgrel=3
pkgdesc="A simple markdown editor/viewer built with PyQt5 for Helwan Linux"
arch=('any')
url="https://github.com/helwan-linux/hel-markdown"
license=('MIT')
depends=('python' 'python-pyqt5' 'python-markdown')
source=("$pkgname::git+https://github.com/helwan-linux/hel-markdown.git")
md5sums=('SKIP')

package() {
    cd "$srcdir/$pkgname"

    # تثبيت السكريبتات
    install -Dm755 main.py "$pkgdir/usr/bin/hel-markdown"
    # غير المسار هنا عشان يكون في نفس مكان main.py
    install -Dm644 translations.py "$pkgdir/usr/bin/translations.py" # <--- التغيير هنا

    # تثبيت الأيقونة
    install -Dm644 icons/halwanmark.png "$pkgdir/usr/share/icons/hicolor/128x128/apps/hel-markdown.png"

    # تثبيت ملف desktop
    install -Dm644 halwanmark.desktop "$pkgdir/usr/share/applications/hel-markdown.desktop"
}
