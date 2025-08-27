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

    # تثبيت جميع ملفات بايثون الضرورية
    install -Dm755 main.py "$pkgdir/usr/bin/hel-markdown"
    install -Dm644 dialogs.py "$pkgdir/usr/bin/dialogs.py"
    install -Dm644 editor.py "$pkgdir/usr/bin/editor.py"
    install -Dm644 file_manager.py "$pkgdir/usr/bin/file_manager.py"
    install -Dm644 format_actions.py "$pkgdir/usr/bin/format_actions.py"
    install -Dm644 search_replace.py "$pkgdir/usr/bin/search_replace.py"
    install -Dm644 theme_manager.py "$pkgdir/usr/bin/theme_manager.py"
    install -Dm644 translations.py "$pkgdir/usr/bin/translations.py"
    install -Dm644 utils.py "$pkgdir/usr/bin/utils.py"

    # تثبيت الأيقونة
    install -Dm644 icons/halwanmark.png "$pkgdir/usr/share/icons/hicolor/128x128/apps/hel-markdown.png"

    # تثبيت ملف سطح المكتب
    install -Dm644 halwanmark.desktop "$pkgdir/usr/share/applications/hel-markdown.desktop"
}
