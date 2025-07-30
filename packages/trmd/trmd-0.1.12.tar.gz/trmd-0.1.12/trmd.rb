class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/4e/e5/ebaff10cb4e479f515a65028ec8c58aab364fb4240a72940e5b80fad917c/trmd-0.1.11.tar.gz"
  sha256 "1cf73f8887891b2657a69b1a4a04209552d5e9e5fa413411c9a509067870037d"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
