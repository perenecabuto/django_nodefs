var NodesTree = function() {}

NodesTree.prototype = {

    renderTree: function(url, parentElement) {
        var that = this;

        $.ajax({ url: url, dataType: 'json', data: {current_url: location.href } })
        .success(function(response) {
            var $nodeTree = $('<nav class="nodefs" />');

            that.buildTree(response, $nodeTree);
            parentElement.append($nodeTree);
            that.prepareEvents();
        });
    },

    prepareEvents: function() {
        var that = this;

        $('.nodefs .node .toggler, .node .label').on('click', function(e) {
            var $node = $(this).closest('.node');

            if (e.target && e.target.href) {
                return;
            }

            if ($node.hasClass('open')) {
                that.closeNode($node);
            } else if ($node.hasClass('closed')) {
                that.openNode($node);
            }
        });

        $('.nodefs .node > .label > a').on('click', function(e) {
            var $node = $(this).closest('.node');

            if ($node.hasClass('selected')) {
                e.preventDefault();
                $(this).closest('.label').trigger('click');
            } else {
                $('.node.selected').removeClass('selected');
                $('[href="' + $(this).attr('href') + '"]').closest('.node').addClass('selected');
            }
        });

        $('[data-tree-collapse-button]').on('click', function() {
            $('.node.open').each(function(idx, node) {
                var $node = $(node);

                that.registerNodeClose($node.attr('id'));
                that.closeNode($node);
            });
        });

        $('[data-tree-expand-button]').on('click', function() {
            $('.node.closed').each(function(idx, node) {
                var $node = $(node);

                that.registerNodeClose($node.attr('id'));
                that.openNode($node);
            });
        });
    },

    openNode: function($node) {
        $node.removeClass('closed').addClass('open');
        this.registerNodeOpen($node.attr('id'));
    },

    closeNode: function($node) {
        $node.removeClass('open').addClass('closed');
        this.registerNodeClose($node.attr('id'));
    },

    nodeWasOpen: function(nodeId) {
        return $.cookie('nodefs_' + nodeId) != null;
    },

    registerNodeOpen: function(nodeId) {
        $.cookie('nodefs_' + nodeId, 'open', { expires: 7, path: '/' });
    },

    registerNodeClose: function(nodeId) {
        $.cookie('nodefs_' + nodeId, null, { expires: 7, path: '/' });
    },

    buildTree: function(tree, parentElement) {
        parentElement.append(this.buildNodeList(tree));
    },

    buildNode: function(node, parentElement) {
        var that = this,
            nodeElement = $('<li/>', { 'class': 'node', id: node.id });

        nodeElement.addClass(this.nodeWasOpen(node.id) ? 'open' : 'closed');

        if (node.selected) {
            nodeElement.addClass('selected');
        }

        if (node.label) {
            nodeElement.append('<span class="label">' + node.label + '</span>');
        }

        if (node.children && node.children.length > 0) {
            nodeElement.append('<span class="toggler" />');
            nodeElement.append(this.buildNodeList(node.children));
        }

        return nodeElement;
    },

    buildNodeList: function(nodeList) {
        var that = this,
            list = [],
            nodeListElement = $('<ul class="tree" />');

        $(nodeList).each(function(idx, node) {
            list.push(that.buildNode(node, nodeListElement));
        });

        nodeListElement.append(list);

        return nodeListElement;
    }
}


$.fn.nodesTree = function(options) {
    var nt = new NodesTree()
        jsonUrl = this.attr('data-url');

    if (options && options.url) {
        jsonUrl = options.url;
    }

    nt.renderTree(jsonUrl, this);
}
